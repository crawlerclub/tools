package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"time"

	"github.com/crawlerclub/httpcache"
	"github.com/liuzl/store"
	"github.com/syndtr/goleveldb/leveldb/util"
)

func main() {
	// Create new FlagSet with only the flags we want
	flags := flag.NewFlagSet("reset_ttl", flag.ExitOnError)
	cacheDir := flags.String("dir", ".httpcache", "Directory for HTTP cache storage")
	policiesFile := flags.String("policies", ".httpcache/policies.txt", "File containing cache policies")
	flags.Parse(os.Args[1:])

	db, err := store.NewLevelStore(*cacheDir + "/data")
	if err != nil {
		log.Fatalf("Failed to initialize cache: %v", err)
	}
	defer db.Close()

	policies, err := httpcache.LoadPoliciesFromFile(*policiesFile)
	if err != nil {
		log.Fatalf("Failed to load cache policies: %+v", err)
	}
	cache := &httpcache.Cache{
		Store:    db,
		Policies: policies,
	}
	count := 0
	if err = db.ForEach(nil, func(key, value []byte) (bool, error) {
		var entry httpcache.CacheEntry
		if err := store.BytesToObject(value, &entry); err != nil {
			log.Printf("Failed to decode cache entry for key %s: %+v", key, err)
			return true, nil
		}
		ttl := cache.GetTTL(entry.URL)
		if ttl <= 0 {
			log.Printf("Skipping %s: no matching policy", entry.URL)
			return true, nil
		}

		entry.ExpiresAt = time.Now().Add(ttl)

		encoded, err := store.ObjectToBytes(entry)
		if err != nil {
			log.Printf("Failed to encode cache entry for %s: %+v", entry.URL, err)
			return true, nil
		}

		if err := db.Put(string(key), encoded); err != nil {
			log.Printf("Failed to update cache entry for %s: %+v", entry.URL, err)
			return true, nil
		}
		count++
		return true, nil
	}); err != nil {
		log.Fatalf("Failed to iterate over cache: %+v", err)
	}

	fmt.Printf("Successfully updated TTL for %d cache entries\n", count)
	if err = db.DB().CompactRange(util.Range{}); err != nil {
		log.Printf("Failed to compact cache: %+v", err)
	} else {
		fmt.Printf("Successfully compacted cache\n")
	}
}

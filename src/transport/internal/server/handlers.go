package server

import (
	"encoding/json"
	"net/http"
	"sync"
	"github.com/evanli135/research-transport/internal/server/models"
	"github.com/evanli135/research-transport/internal/server/sources"
)


// fetchHandler fans out to all requested sources concurrently,
// collects results, and returns a unified response.
func fetchHandler(write http.ResponseWriter, read *http.Request) {
	if read.Method != http.MethodPost {
		http.Error(write, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req models.FetchRequest
	if err := json.NewDecoder(read.Body).Decode(&req); err != nil {
		http.Error(write, "Invalid Request Body", http.StatusBadRequest)
		return
	}
	
	// Default to all sources if none are specified
	requested := req.Sources
	if len(requested) == 0 {
		requested = []string{"semantic_scholar", "arxiv"}
	}

	// Write each into a mutex for safety
	var (
		mu sync.Mutex
		papers []models.Paper
		errs []models.Error
		wg 		sync.WaitGroup
	)

	for _, source := range requested {
		wg.Add(1)

		go func(source string) {
			defer wg.Done()

			var (
				result []models.Paper
				err   error
			)

			switch source {
				case "semantic_scholar":
					result, err = sources.FetchSemanticScholar(req.Query, req.Limit)
				case "arxiv":
					result, err = sources.FetchArxiv(req.Query, req.Limit)
			
					default:
				mu.Lock()
				errs = append(errs, models.Error{Source: source, Message: "unknown source"})
				mu.Unlock()
				return
			}

			mu.Lock()
			if err != nil {
				errs = append(errs, models.Error{Source: source, Message: err.Error()})
			} else {
				papers = append(papers, result...)
			}
			mu.Unlock()
		} (source)
	}

	wg.Wait()

	write.Header().Set("Content-Type", "application/json")
	json.NewEncoder(write).Encode(models.FetchResponse{
		Papers: papers,
		Errors: errs,
	})
}

func healthHandler(writer http.ResponseWriter, reader *http.Request) {
	writer.Header().Set("Content-Type", "application/json")
	writer.Write([]byte(`{"status":"ok"}`))
}
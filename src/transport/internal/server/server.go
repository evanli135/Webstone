
package server
 
import (
	"fmt"
	"log"
	"net/http"
)
 
func Start(port int) {
	mux := http.NewServeMux()
 
	mux.HandleFunc("/fetch", fetchHandler)
	mux.HandleFunc("/health", healthHandler)
 
	addr := fmt.Sprintf(":%d", port)
	log.Printf("transport service listening on %s", addr)
 
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatalf("server error: %v", err)
	}
}
 
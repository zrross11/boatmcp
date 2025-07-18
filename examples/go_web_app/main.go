package main

import (
	"fmt"
	"log"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Hello, from your Go sample application!")
}

func main() {
	http.HandleFunc("/", handler)
	fmt.Println("Go server listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

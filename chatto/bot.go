package bot

import (
	"net/http"
	"path"

	"github.com/jaimeteb/chatto/bot"
)

var b *bot.Server

const (
	sourceCodePath = "./serverless_function_source_code/"
	chattoDataPath = "data/"
)

func init() {
	b = bot.NewServer(path.Join(sourceCodePath, chattoDataPath), 0)
}

// TelegramHandler wrapper
func TelegramHandler(w http.ResponseWriter, r *http.Request) {
	b.TelegramHandler(w, r)
}

// RESTHandler wrapper
func RESTHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Add("Access-Control-Allow-Origin", "*")
	w.Header().Add("Access-Control-Allow-Methods", "POST")
	w.Header().Add("Access-Control-Allow-Headers", "Content-Type, Authorization")
	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusNoContent)
	} else {
		b.RESTHandler(w, r)
	}
}

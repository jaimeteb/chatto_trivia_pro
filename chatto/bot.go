package bot

import (
	"net/http"
	"path"

	"github.com/GoogleCloudPlatform/functions-framework-go/functions"
	"github.com/jaimeteb/chatto/bot"
)

var b *bot.Server

const (
	sourceCodePath = "./serverless_function_source_code/"
	chattoDataPath = "data/"
)

func init() {
	b = bot.NewServer(path.Join(sourceCodePath, chattoDataPath), 0)
	if false {
		functions.HTTP("RESTHandler", RESTHandler)
		functions.HTTP("TelegramHandler", TelegramHandler)
	}
}

// TelegramHandler wrapper
func TelegramHandler(w http.ResponseWriter, r *http.Request) {
	b.TelegramHandler(w, r)
}

// RESTHandler wrapper
func RESTHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Add("Access-Control-Allow-Origin", "*")
	w.Header().Add("Access-Control-Allow-Methods", "POST")
	if r.Method == "OPTIONS" {
		w.WriteHeader(http.StatusNoContent)
		return
	}

	b.RESTHandler(w, r)
}

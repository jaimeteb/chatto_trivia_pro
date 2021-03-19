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

// RESTHandler wrapper
func RESTHandler(w http.ResponseWriter, r *http.Request) {
	b.RESTHandler(w, r)
}


# HTTP(S) - Client 

## Функционал:
*CLI

*Указание урла

*Указание метода запроса (get, post, …)

*Указание тела запроса

*Указание хедеров

*Таймаут ожидания ответа

*Возможность сохранить данные из ответа в файл

*Поддержка cookie

*URL для теста прогрессбара(по этому урлу большое тело запроса, видно как работает бар)
```
https://raw.githubusercontent.com/dwyl/english-words/master/words.txt
```
Также замечу, что прогресс бар отображается только для тех ответов, в которых есть заголовок Content-Length, то есть где Transfer-Encoding: chunked(нет заголовка Content-Length), прогрессбара нет, ибо нельзя сразу узнать длину всего тела сообщения

-----------------------------------------------------------------------------------------------------------------------------------  
## Usage:
```
python3 -m <URL> [OPTIONS]
```
-----------------------------------------------------------------------------------------------------------------------------------
## Example:
```
python3 -m https://vk.com -H User-Agent Yandex -M GET
```

| Argument | Action                  | Using Examples       | 
|----------|-------------------------|----------------------|
| -d       | Set data                | -d "Hello, World!"   |
| -F       | Write output in file    | -f "test.txt"        |
| -H       | Add headers(Split by $) | -H User-Agent Yandex |
| -M       | Choose request method   | -m POST              |
| -c       | add cookie              | -c "income=1"        |
| -t       | Set timeout             | -t 3000              |
| -v       | Show response headers   | -v                   |


###Example for connect via http and IP:
``
python3 -m app http://46.17.203.154
``

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


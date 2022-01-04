
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

```
https://raw.githubusercontent.com/dwyl/english-words/master/words.txt
```

-----------------------------------------------------------------------------------------------------------------------------------  
## Usage:
```
python3 -m app <URL> [OPTIONS]
```
-----------------------------------------------------------------------------------------------------------------------------------
## Example:
```
python3 -m app https://vk.com -H User-Agent Yandex -M GET
```

| Argument | Action                   | Using Examples           | 
|----------|--------------------------|--------------------------|
| -b       | Set body                 | -b "Hello, World!"       |
| -F       | Write output in file     | -f "test.txt"            |
| -H       | Add headers              | -H "User-Agent: Yandex"  |
| -M       | Choose request method    | -m POST                  |
| -t       | Set timeout              | -t 3000                  |
| -r       | Allow redirects          | -v                       |
| -l       | Dont print response body | -v                       |
| -v       | Show response headers    | -v                       |
| -s       | Stream answer            | -v                       |

###Example for connect via http and IP:
``
python3 -m app http://46.17.203.154
``
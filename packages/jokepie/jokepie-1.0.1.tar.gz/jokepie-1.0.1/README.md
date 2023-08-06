# JokeAPI Wrapper by TheWever
### Import jokeapie
```
import jokepie # imports package
```

### Create a client
```
client = jokepie.Client() # returns client objects
```

### Get a joke
```
joke = client.get_joke() # returns Joke object
```

### Post a joke
```
client.upload_joke('Insert Joke', 'category') # returns True on exception
```

### Sample:
```
import jokepie
client = jokepie.Client()
joke = client.get_joke('dog')
print(joke.joke)
```
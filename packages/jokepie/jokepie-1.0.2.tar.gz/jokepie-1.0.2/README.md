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

## Docs
###Joke Objetct:
- Category # returns
- joke_type # returns str
- joke # returns str or list
- flags # returns list
- id # returns int
- safe # return bool
- language / lang # returns str
- request # returns req resp object
- get\_joke() # returns joke or dict

###Client Object:
- get\_joke(content='', lang='english', categories: list=['any'], blacklist=[], joke_type='single', safe_mode=False, id_range=[], amount: int = 1) # returns Joke Object
- upload\_joke(joke: str or dict, category, joke_type='single', lang='english', on_flags=[]) # returns bool

--
#Notes:
##Given Args
Most arguments are not required but should be checked especially before uploading a joke
##Sequence Matcher
When you provide an invalid argument like inglish as language the best match will be choosen using SequenceMatcher
##Uploading jokes
When you want to upload a joke of the type twopart provide a list[setup, delivery] as joke else str(joke)
##Updates and async
This libary will not recive any updates only patches and is not asynchronous
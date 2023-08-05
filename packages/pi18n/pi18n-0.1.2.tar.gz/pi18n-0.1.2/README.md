# Pi18n
Pi18n is an internationalization library for Python

## Installation
Install using pip
```shell
pip install pi18n
```

## Getting started
Pi18n lets you internationalize your Python app in a simple way. It works like this:
- Provide Pi18n with as many JSON files as languages your app is going to support.
  - Each file will be named with the locale of the language it represents.
  - The content that is going to be placed in the app will be in each of these files, translated into the language that 
  the file represents and associated with a code. 
  - The way a translation is associated with a code is by a JSON object: each key of the object is the code, and the value
  is the translation associated to the code for every language.
  - Every JSON object of every file must have the same keys.
  - Translations can contain named parameters (placeholders) that will be replaced by a certain value on translation-time. Provide 
  as many as needed with this syntax: `{param-code}`.
- Instantiate an object of `TranslationService` class. Its constructor must receive:
  1. The path with the translation files.
  2. The default locale.
- Call the `get` method of the `TranslationService` instance for getting a translation:
  1. Provide the translation code to the `get` method as the first argument.
  2. Optionally, provide parameters to the translation either as a dict or as keyword arguments.

## Usage
### 1. Place some translation files in your project
**resources/es.json**
```json
{
  "HELLO_WORLD": "Hola mundo!",
  "WITH_PARAMS": "Los parámetros son: {fruit1}, {fruit2} and {fruit3}"
}
```
**resources/en.json**
```json
{
  "HELLO_WORLD": "Hello world!",
  "WITH_PARAMS": "Params are: {fruit1}, {fruit2} and {fruit3}"
}
```

### 2. Create an instance of `TranslationService`
**main.py**
```python
from pi18n import TranslationService

translation_service = TranslationService('resources', 'es')
```

### 3. Use the `TranslationService`
Get a translation:

```python
translation = translation_service.get("HELLO_WORLD")
print(f"Message in Spanish: {translation}")

>>> "Message in Spanish: Hola mundo!"
```

Change locale at runtime:

```python
translation_service.change_locale("en")
translation = translation_service.get("HELLO_WORLD")
print(f"Message in English: {translation}")

>>> "Message in English: Hello world!"
```

Get a translation that receives some params as a dict:
```python
params = {"fruit1": "apple", "fruit2": "orange", "fruit3": "banana"}
translation = translation_service.get("WITH_PARAMS", params)
print(f"Message with params: {translation}")

>>> "Message with params: Params are: apple, orange and banana"
```

Get a translation that receives some params as kerword arguments:
```python
translation = translation_service.get("WITH_PARAMS", fruit1="apple", fruit2="orange", fruit3="banana")
print(f"Message with params: {translation}")

>>> "Message with params: Params are: apple, orange and banana"
```
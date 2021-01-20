# Spotify WordCloud

![Lint + Format](https://github.com/HelloRusk/spotify-wordcloud/workflows/Lint%20+%20Format/badge.svg)

English · [日本語](./docs/README_ja.md)

---

<br>
<div align="center">
  <img src="https://res.cloudinary.com/hellorusk/image/upload/v1611156028/top.png" width="80%">
</div>
<br>

Spotify WordCloud is an app that lets you create a word cloud from the names of your favorite artists.  
You can tweet the word cloud on the spot. You can also save the word cloud and look back at it later.  

https://spotify-wordcloud.herokuapp.com/  
(currently only available in Japanese)

## Test locally

### Requirements

- Python 3.8
- Spotify Account
- Twitter Account
- AWS Account (to save images in Amazon S3)

### Installation

```
$ git clone https://github.com/HelloRusk/spotify-wordcloud
$ cd spotify-wordcloud
$ pip install -r requirements.txt
```

### Configuration

Set local environment variables in `.env`.  
You can refer to `.env.example`.

### Run server

```
$ FLASK_DEBUG=True OAUTHLIB_INSECURE_TRANSPORT=1 python run.py
```

and open `http://127.0.0.1:5000/`.

## URL

| Path   |  Method  |  Description  |
|:---|:---|:---|
|  /  |  GET  |  Display the top screen  |
|  /login  |  GET  |   Log in to Spotify |
| /login/spotify/authorized |GET |  Callback for Spotify OAuth authentication  |    
|  /twitter_auth  |  GET  |  Log in to Twitter  |    
|  /callback  |  GET  |  Callback for Twitter OAuth authentication  |    
|  /logout  | GET   |  Log out all (destroy session)  |   
|  /generate  |  GET  |  Create a word cloud image and return its binary  |    
|  /regenerate  |  GET  | Create a word cloud image and return its binary <br>(Unlike /generate method, it forces re-creation even if there is a cache)  |  
|  /save  |  POST  |  Create a word cloud image, upload the image to S3, and save it in the DB with user ID and creation date   |    
|  /tweet  |  POST  | Create a word cloud image and tweet it   |    
|  /history  | GET   | Display the list of images created in the past  |    
|  /history/:file_hash  |  DELETE  |  Delete the specified image  |    

#### Learn more about creating word cloud images

This app retrieves the list of top artists from Spotify's "Get a User's Top Artists" API, combines them into a single string, and creates a word cloud based on it.  
The combined string is kept in the session. The image is placed in the `/tmp` folder with the hash of the string as the file name.    
URLs related to image creation will always try to refer to these cached information first. However, /regenerate does not refer to the `/tmp` folder, and creates the image again.  
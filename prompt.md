# Singing Servos

Project Summary: Code to use a Raspberry PI Zero 2 W to control servos connected to the mouths of various robots, so that when a song is played (via the Pi), the servos move in concert with the vocals of the song, to make it appear as if the robots are singing. 

## Key points
- Project should be in Python
- Code will run on Pi directly
- Three servos
- PI servo controlling code
- Something that can take MP3 songs, detect the vocals and such, and convert it into something that will allow us to control the servos
- Should be able to accept basically any mp3 song and find vocals in it
- Ideally each servo would be treated separately, that way we could have specific robots speak specific parts. 
- Plays out of a speaker connected to the Pi, somehow
- Mouth movements by the servo should be natural, on syllables and such, not just "open when singing"
- We should be able to have specific servos sing specific parts. Like, if its a call and response song, maybe one servo would sing the call and the others sing the response. I can't visualize this though, I don't know how we would delineate between the two in our conversion into something the servo can understand. 
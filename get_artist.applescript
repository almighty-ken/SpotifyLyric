-- Creates a notification with information about the currently playing track

-- Main flow
set currentlyPlayingTrack to getCurrentlyPlayingTrack()
return currentlyPlayingTrack

-- Method to get the currently playing track
on getCurrentlyPlayingTrack()
	tell application "Spotify"
		set currentArtist to artist of current track as string
		
		return currentArtist
	end tell
end getCurrentlyPlayingTrack

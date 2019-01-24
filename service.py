import xbmcaddon
import xbmcgui
import xbmc
import requests

__addon__ = xbmcaddon.Addon()
__addon_name__ = __addon__.getAddonInfo('name')
__api_url__ = __addon__.getSetting('apiAddress') + 'plum-lightpad-php-api/'


def started_playing():
    dim = float(__addon__.getSetting('moviePlayDim'))
    # If VideoPlayer.TVShowTitle is not empty then we know it's a TV Show so we set the dim to the tvPlayDim
    if xbmc.getInfoLabel('VideoPlayer.TVShowTitle'):
        dim = float(__addon__.getSetting('tvPlayDim'))
    set_lightpad_dim(dim)


def paused_playing():
    set_lightpad_dim(float(__addon__.getSetting('pauseDim')))


def set_lightpad_dim(dim_level):
    # Convert the value to accommodate for plum's weird leveling in their api?
    dim_level = dim_level * 2.55
    if dim_level == 0:
        return
    try:
        # For some odd reason when we make a PUT request the server doesn't register the params
        # So I just made it a GET request and it works fine.
        request = requests.get(__api_url__ + 'set_lightpad_dim.php', {'dim': dim_level})
        response = request.content.decode('utf-8')
        if response == 'An error occurred':
            xbmcgui.Dialog().notification(__addon_name__, 'Bad reply from light server: ' + str(request.status_code))
    except requests.exceptions.RequestException as error:
        xbmcgui.Dialog().notification(__addon_name__, 'Cannot reach light server')
        xbmc.log(error.strerror)


def main():
    is_playing = False
    # Infinite loop
    while not xbmc.Monitor().abortRequested():
        # Sleep/wait for abort for 1 second
        # We wait 1 second between each check since there is no point of checking every tick and affecting performance.
        if xbmc.Monitor().waitForAbort(1):
            # Abort was requested while waiting. We should exit
            break
        # https://kodi.wiki/view/List_of_boolean_conditions#Player
        if xbmc.getCondVisibility('Player.Playing'):
            if not is_playing:
                started_playing()
                is_playing = True
        elif xbmc.getCondVisibility('Player.Paused') and is_playing:
            paused_playing()
            is_playing = False
        elif not xbmc.getCondVisibility('Player.Playing') and is_playing:
            paused_playing()
            is_playing = False


# Called when xbmc is started
if __name__ == '__main__':
    main()
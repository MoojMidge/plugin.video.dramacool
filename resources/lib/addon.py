from xbmcgui import Dialog, ListItem

import base64
import edb
import idb
import os
import plugin
import request
import resolveurl
import xbmc
import xbmcaddon
import xbmcplugin

_addon = xbmcaddon.Addon()
_localizedstr = _addon.getLocalizedString
_plugins = os.path.join(xbmc.translatePath(_addon.getAddonInfo('path')), 'resources/lib/resolveurl/plugins')


@plugin.route('/')
def _():
    show([(plugin.url_for('/search?type=movies'), ListItem(_localizedstr(33000)), True),
          (plugin.url_for('/search?type=stars'), ListItem(_localizedstr(33001)), True),
          (plugin.url_for('/recently-viewed'), ListItem(_localizedstr(33002)), True),
          (plugin.url_for('/recently-added?page=1'), ListItem(_localizedstr(33003)), True),
          (plugin.url_for('/recently-added-movie?page=1'), ListItem(_localizedstr(33004)), True),
          (plugin.url_for('/recently-added-kshow?page=1'), ListItem(_localizedstr(33005)), True),
          (plugin.url_for('/drama-list'), ListItem(_localizedstr(33006)), True),
          (plugin.url_for('/drama-movie'), ListItem(_localizedstr(33007)), True),
          (plugin.url_for('/kshow'), ListItem(_localizedstr(33008)), True),
          (plugin.url_for('/most-popular-drama?page=1'), ListItem(_localizedstr(33009)), True),
          (plugin.url_for('/list-star.html?page=1'), ListItem(_localizedstr(33010)), True)])


@plugin.route(r'/search\?type=(movies|stars)')
def _():
    keyboard = xbmc.Keyboard()
    keyboard.doModal()

    if keyboard.isConfirmed():
        plugin.redirect(plugin.pathquery + '&keyword=' + keyboard.getText() + '&page=1')


@plugin.route(r'/search\?((type=movies|type=stars|page=[^&]+|keyword=[^&]+)&?)+')
def _():
    items = []

    if 'movies' in plugin.query['type']:
        (dramalist, paginationlist) = request.dramapaginationlist(plugin.pathquery)
        idb.connect()

        for path in dramalist:
            (poster, detail) = idb.fetchone(path)
            item = ListItem(detail['title'])
            item.setArt({'poster': poster})
            item.setInfo('video', detail)
            items.append((plugin.url_for(path), item, True))

        idb.close()
    else:
        (starlist, paginationlist) = request.starsearchpaginationlist(plugin.pathquery)

        for (path, poster, title) in starlist:
            item = ListItem(title)
            item.setArt({'poster': poster})
            items.append((plugin.url_for(path), item, True))

    for (query, title) in paginationlist:
        item = ListItem(_localizedstr(33600 if title == 'next' else 33601))
        items.append((plugin.url_for(plugin.path + query), item, True))

    show(items)


@plugin.route('/recently-viewed')
def _():
    edb.connect()
    idb.connect()
    items = []

    for path in edb.fetchall():
        (poster, detail) = idb.fetchone(path)
        item = ListItem(detail['title'])
        item.addContextMenuItems([
            (_localizedstr(33100), 'RunPlugin(plugin://plugin.video.dramacool/recently-viewed?delete=' + path + ')'),
            (_localizedstr(33101), 'RunPlugin(plugin://plugin.video.dramacool/recently-viewed?delete=%)')])
        item.setArt({'poster': poster})
        item.setInfo('video', detail)
        items.append((plugin.url_for(path), item, True))

    edb.close()
    idb.close()
    show(items)


@plugin.route(r'/recently-viewed\?delete=(?P<delete>.+)')
def _(delete):
    edb.connect()
    edb.remove(delete)
    edb.close()
    xbmc.executebuiltin('Container.Refresh')


@plugin.route(r'/recently-added\?page=[^&]+')
@plugin.route(r'/recently-added-movie\?page=[^&]+')
@plugin.route(r'/recently-added-kshow\?page=[^&]+')
def _():
    (recentlylist, paginationlist) = request.recentlypaginationlist(plugin.pathquery)
    items = []

    for (path, poster, title) in recentlylist:
        item = ListItem(title)
        item.setArt({'poster': poster})
        item.setInfo('video', {})
        item.setProperty('IsPlayable', 'true')
        items.append((plugin.url_for(path), item, False))

    for (query, title) in paginationlist:
        item = ListItem(_localizedstr(33600 if title == 'next' else 33601))
        items.append((plugin.url_for(plugin.path + query), item, True))

    show(items)


@plugin.route('/drama-list')
def _():
    show([(plugin.url_for('/category/korean-drama'), ListItem(_localizedstr(33200)), True),
          (plugin.url_for('/category/japanese-drama'), ListItem(_localizedstr(33201)), True),
          (plugin.url_for('/category/taiwanese-drama'), ListItem(_localizedstr(33202)), True),
          (plugin.url_for('/category/hong-kong-drama'), ListItem(_localizedstr(33203)), True),
          (plugin.url_for('/category/chinese-drama'), ListItem(_localizedstr(33204)), True),
          (plugin.url_for('/category/other-asia-drama'), ListItem(_localizedstr(33205)), True),
          (plugin.url_for('/category/thailand-drama'), ListItem(_localizedstr(33206)), True)])


@plugin.route('/drama-movie')
def _():
    show([(plugin.url_for('/category/korean-movies'), ListItem(_localizedstr(33300)), True),
          (plugin.url_for('/category/japanese-movies'), ListItem(_localizedstr(33301)), True),
          (plugin.url_for('/category/taiwanese-movies'), ListItem(_localizedstr(33302)), True),
          (plugin.url_for('/category/hong-kong-movies'), ListItem(_localizedstr(33303)), True),
          (plugin.url_for('/category/chinese-movies'), ListItem(_localizedstr(33304)), True),
          (plugin.url_for('/category/american-movies'), ListItem(_localizedstr(33305)), True),
          (plugin.url_for('/category/other-asia-movies'), ListItem(_localizedstr(33306)), True),
          (plugin.url_for('/category/thailand-movies'), ListItem(_localizedstr(33307)), True)])


@plugin.route('/category/[^/]+')
@plugin.route('/kshow')
def _():
    show([(plugin.url_for(plugin.path + '/char'), ListItem(_localizedstr(33400)), True),
          (plugin.url_for(plugin.path + '/year'), ListItem(_localizedstr(33401)), True),
          (plugin.url_for(plugin.path + '/status'), ListItem(_localizedstr(33402)), True)])


@plugin.route('(?P<path>/category/[^/]+)/(?P<selectid>[^/]+)')
@plugin.route('(?P<path>/kshow)/(?P<selectid>[^/]+)')
def _(path, selectid):
    items = []

    for selectvalue in request.filterlist(path, selectid == 'char', selectid == 'year', selectid == 'status'):
        item = ListItem(selectvalue)
        items.append((plugin.url_for(plugin.path + '/' + base64.b64encode(selectvalue).decode('ascii')), item, True))

    show(items)


@plugin.route('(?P<path>/category/[^/]+)/(?P<selectid>[^/]+)/(?P<selectvalue>[^/]+)')
@plugin.route('(?P<path>/kshow)/(?P<selectid>[^/]+)/(?P<selectvalue>[^/]+)')
def _(path, selectid, selectvalue):
    selectvalue = base64.b64decode(selectvalue).decode('ascii')
    idb.connect()
    items = []

    if selectid == 'char':
        dramalist = request.dramalist(path, filterchar=selectvalue)
    elif selectid == 'status':
        dramalist = request.dramalist(path, filterstatus='status_' + selectvalue)
    else:
        dramalist = request.dramalist(path, filteryear='year_' + selectvalue)

    for path in dramalist:
        (poster, detail) = idb.fetchone(path)
        item = ListItem(detail['title'])
        item.setArt({'poster': poster})
        item.setInfo('video', detail)
        items.append((plugin.url_for(path), item, True))

    idb.close()
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    show(items)


@plugin.route(r'/most-popular-drama\?page=[^&]+')
def _():
    (dramalist, paginationlist) = request.dramapaginationlist(plugin.pathquery)
    idb.connect()
    items = []

    for path in dramalist:
        (poster, detail) = idb.fetchone(path)
        item = ListItem(detail['title'])
        item.setArt({'poster': poster})
        item.setInfo('video', detail)
        items.append((plugin.url_for(path), item, True))

    for (query, title) in paginationlist:
        item = ListItem(_localizedstr(33600 if title == 'next' else 33601))
        items.append((plugin.url_for(plugin.path + query), item, True))

    idb.close()
    show(items)


@plugin.route(r'/list-star.html\?page=[^&]+')
def _():
    (starlist, paginationlist) = request.starpaginationlist(plugin.pathquery)
    items = []

    for (path, poster, title, plot) in starlist:
        item = ListItem(title)
        item.setArt({'poster': poster})
        item.setInfo('video', {'plot': plot})
        items.append((plugin.url_for(path), item, True))

    for (query, title) in paginationlist:
        item = ListItem(_localizedstr(33600 if title == 'next' else 33601))
        items.append((plugin.url_for(plugin.path + query), item, True))

    show(items)


@plugin.route('/star/[^/]+')
def _():
    idb.connect()
    items = []

    for path in request.stardramalist(plugin.path):
        (poster, detail) = idb.fetchone(path)
        item = ListItem(detail['title'])
        item.setArt({'poster': poster})
        item.setInfo('video', detail)
        items.append((plugin.url_for(path), item, True))

    idb.close()
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    show(items)


@plugin.route('/drama-detail/.+')
def _():
    edb.connect()
    edb.add(plugin.path)
    edb.close()
    items = []

    for (path, title) in reversed(request.episodelist(plugin.path)):
        item = ListItem(title)
        item.setInfo('video', {})
        item.setProperty('IsPlayable', 'true')
        items.append((plugin.url_for(path), item, False))

    show(items)


@plugin.route('/[^/]+.html', order=1)
def _():
    (serverlist, titlelist, title) = request.serverlist(plugin.path)
    position = Dialog().select(_localizedstr(33500), titlelist)

    if position != -1:
        xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
        resolveurl.add_plugin_dirs(_plugins)

        try:
            url = resolveurl.resolve(serverlist[position])

            if url:
                item = ListItem(title, path=url)
                subtitle = request.subtitle(serverlist[position])

                if subtitle is not None:
                    item.setSubtitles([subtitle])

                xbmcplugin.setResolvedUrl(plugin.handle, True, item)
            else:
                raise
        except:
            Dialog().notification(_localizedstr(33501), '')

        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')


def show(items):
    xbmcplugin.setContent(plugin.handle, 'videos')
    xbmcplugin.addDirectoryItems(plugin.handle, items, len(items))
    xbmcplugin.endOfDirectory(plugin.handle)


if __name__ == '__main__':
    plugin.run()

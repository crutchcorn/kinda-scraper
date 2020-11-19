import re

from bs4 import BeautifulSoup


def findImgSrc(imgEl):
    srcset = getattr(imgEl, 'srcset', False)
    if not srcset:
        try:
            srcset = imgEl['data-srcset']
        except:
            0
    if not srcset:
        src = getattr(imgEl, 'src', False)
        if not src:
            return ['', '']
        src_ids = re.findall(r'^.*\/(.*?)$', src)
        if len(src_ids) == 0 or src_ids[0].startswith('http'):
            return ['', '']
        return [f'https://i.kinja-img.com/gawker-media/image/upload/{src_ids[0]}', src_ids[0]]
    img_ids = re.findall(r'^.*\/(.*?)\s80w', srcset)
    return [f'https://i.kinja-img.com/gawker-media/image/upload/{img_ids[0]}', img_ids[0]]


def findVidSrc(vidEl):
    postersrc = vidEl['data-postersrc']
    if not postersrc:
        return ['', '']
    vid_ids = re.findall(r'^.*\/(.*?)\..*?$', postersrc)
    return [f'https://i.kinja-img.com/gawker-media/image/upload/{vid_ids[0]}.mp4', f'{vid_ids[0]}.mp4']


html_doc = '';

with open('demo.html', 'r', encoding="utf8") as file:
    html_doc = file.read()

soup = BeautifulSoup(html_doc, 'html.parser')

# Remove ads
[x.extract() for x in soup.findAll(class_='swappable-mobile-ad-container')]
[x.extract() for x in soup.findAll(class_='ad-mobile-dynamic')]
[x.extract() for x in soup.findAll(class_='movable-ad')]

# Remove magnifying glass
[x.extract() for x in soup.findAll(class_='magnifier')]

for imageWrapper in soup.findAll(class_="image-hydration-wrapper"):
    # For some reason, image wrappers have a padding-bottom of a lot. Remove them and move on
    imageWrapper['style'] = ''

for videoOrImgContainer in soup.findAll(class_="js_lazy-image"):
    vid = videoOrImgContainer.find('video')
    img = videoOrImgContainer.find('img')
    if not not vid:
        _, vidSrc = findVidSrc(vid)
        vid.attrs = {}
        vid.clear()
        source = soup.new_tag('source')
        source['type'] = "video/mp4"
        source['src'] = "./" + vidSrc
        vid.append(source)
        videoOrImgContainer.replace_with(vid)
    if not not img:
        alt = img['alt']
        _, imgSrc = findImgSrc(img)
        img.attrs = {}
        img['alt'] = alt
        img['src'] = "./" + imgSrc
        videoOrImgContainer.replace_with(img)

for iframe in soup.findAll('iframe'):
    recId = ''
    try:
        recId = iframe['data-recommend-id']
    except:
        continue
    ytId = re.findall(r'youtube:\/\/(.*)', recId)
    if not ytId[0]:
        continue
    newSrc = 'https://www.youtube.com/embed/' + ytId[0]
    newIframe = BeautifulSoup('<iframe width="560" height="315" src="' + newSrc + '" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>', 'html.parser')
    iframe.replace_with(newIframe)

print(soup)

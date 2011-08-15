import xml.dom.minidom as minidom

from BeautifulSoup import BeautifulSoup

import utils

def articles_from_xml(xml):
    def getText(root, name):
        el = root.getElementsByTagName(name)[0]
        nodelist = el.childNodes
        rc = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return u''.join(rc)

    dom = minidom.parseString(xml)
    components = dom.getElementsByTagName("NewsComponent")[1:]
    for component in components:
        newsref = component.getElementsByTagName("NewsItemRef")[0]
        link = newsref.getAttribute("NewsItem")
        newslines = component.getElementsByTagName("NewsLines")[0]
        date = getText(newslines, "DateLine")
        title = getText(newslines, "HeadLine")
        yield link, utils.isodate(date), title

def links_in_article(html):
    soup = BeautifulSoup(html)

    def link_from_tag(tag):
        link_tag = tag.a
        if link_tag:
            if link_tag.has_key('href'):
                link = link_tag['href'].strip()
                if len(link) < 10:
                    return None
                elif link.startswith('/'):
                    link_tag['href'] = 'http://www.nhs.uk' + link
                else:
                    link_tag['href'] = link
                return link_tag['href']
        return None

    def parse_tag(tag):
        link = link_from_tag(tag)
        html = unicode(tag.renderContents(), "utf-8")
        return link, html

    def tags_in_div(clazz):
        for link_div in soup.findAll('div', {"class":clazz}):
            for tag in link_div.findAll(text=False):
                yield tag

    type = 'headline'
    for tag in tags_in_div('further-reading'):
        if tag.string == 'Links to the headlines':
            type = 'headline'
        elif tag.string == 'Links to the science':
            type = 'science'
        elif tag.name == 'p':
            link, html = parse_tag(tag)
            if link:
                yield type, html, link

    type = 'useful'
    for tag in tags_in_div('panel-top'):
        if tag.string == 'Useful links':
            type = 'useful'
        if tag.string == 'Related articles':
            type = 'related'
        elif tag.name == 'ul':
            for listitem in tag.findAll('li'):
                link, html = parse_tag(listitem)
                if link:
                    yield type, html, link

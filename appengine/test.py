import urllib

import parsers

file = urllib.urlopen("http://www.nhs.uk/news/2010/03March/Pages/Impotence-is-a-warning-sign-for-heart-risk.aspx")
for tag in parsers.links_in_article(file.read()):
    print tag

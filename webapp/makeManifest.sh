#!/bin/bash

echo "CACHE MANIFEST" > webapp.manifest && echo "CACHE:" >> webapp.manifest && find . | grep ".gif\|.jpg\|.png\|.css\|.html\|.js\|.ttf\|.ogv\|.mp4\|.ogg\|.mp3" >> webapp.manifest

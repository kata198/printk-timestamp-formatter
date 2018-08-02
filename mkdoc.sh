#!/bin/bash

shopt -s nullglob
ALL_MODS="$(echo printk_timestamp_converter/**.py printk_timestamp_converter/**/*.py | tr ' ' '\n' | sed -e 's|/|.|g' -e 's|.py$||g' -e 's|.__init__$||g' | tr '\n' ' ')"

pydoc -w ${ALL_MODS}
mv printk_timestamp_converter*.html doc/
pushd doc >/dev/null 2>&1
rm -f index.html

for fname in `echo *.html`;
do
    python <<EOT

import AdvancedHTMLParser
import sys

if __name__ == '__main__':

    filename = "${fname}"

    parser = AdvancedHTMLParser.AdvancedHTMLParser()
    parser.parseFile(filename)

    em = parser.filter(tagName='a', href='.')

    if len(em) == 0:
        sys.exit(0)

    em = em[0]

    em.href = 'printk_timestamp_converter.html'

    parentNode = em.parentNode

    emIndex = parentNode.children.index(em)

    i = len(parentNode.children) - 1
    
    while i > emIndex:
        parentNode.removeChild( parentNode.children[i] )
        i -= 1


    with open(filename, 'wt') as f:
        f.write(parser.getHTML())


EOT


done

ln -s printk_timestamp_converter.html index.html

popd >/dev/null 2>&1

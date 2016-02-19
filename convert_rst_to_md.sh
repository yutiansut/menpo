
# 1. Convert the userguide to markdown
cd ./docs/api/source/userguide
for file in *.rst
do 
  pandoc -f rst -t markdown_github -o ../../../book/userguide/${file%%.*}.md $file
done
cp *.jpg ../../../book/userguide/

# 2. Convert the API docs index to markdown
cd ..
pandoc -f rst -t markdown_github -o ../../book/userguide.md index.rst

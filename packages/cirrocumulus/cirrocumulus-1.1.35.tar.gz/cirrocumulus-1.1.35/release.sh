set -e

git tag -a 1.1.35 -m "1.1.35"
git push origin --tags
git pull
rm -rf node_modules
rm -rf dist
yarn install
yarn build
python -m build
python3 -m twine upload dist/*

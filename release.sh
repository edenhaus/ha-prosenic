#Script to cerate the release.zip

# Clean the dist directory
RELEASE=release

rm -vR $RELEASE
mkdir $RELEASE

# zip the prosenic sources
zip -jr $RELEASE/prosenic.zip custom_components/prosenic
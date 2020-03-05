#Script to cerate the release.zip

# Clean the dist directory
RELEASE=release

rm -vR $RELEASE
mkdir $RELEASE

# zip the prosenic sources
cd custom_components/prosenic; zip -r ../../$RELEASE/prosenic.zip . -x "__pycache__/*"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# For Rpi0 (Armv6)
if [ ! -d $DIR/build ]; then
	mkdir $DIR/build
fi
cd $DIR/build


cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo $DIR
	
make -j

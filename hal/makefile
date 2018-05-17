client:
	g++ client.c -D CPP_PROG -o client	

all: clean client server
	g++ server.c -D CPP_PROG -o server

clean:
	rm -f server
	rm -f client
	rm -rf INCA_libs
	rm -rf *.o
	rm -rf *.pyc

c_code: 
	gcc  -m32 -fpic server.c -shared -o ./lib/libdpi.so

sim: clean client
	irun -access +rwc -gui -sv -sv_lib ./lib/libdpi.so tb.sv

build: 
	swig -python client.i
	gcc -fPIC -c client.c client_wrap.c -I/home/prya/usr/include/python2.7
	ld -shared client.o client_wrap.o -o _client.so

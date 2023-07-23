#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/fb.h>
#include <time.h>


int main(int argc, char *argv[])
{
	//------------------------------------------------------------
	//    CHECK ARGS
	//------------------------------------------------------------

	if (argc != 3)
	{
		printf("USAGE:\n");
		printf("dfb2 </dev/graphics/fb0> <SCREEN UPDATE RATE>\n");
		return -1;
	}

	char *dev = argv[1];

	int rate = strtol(argv[2], 0, 10);

	//------------------------------------------------------------
	//    OPEN DEVICE
	//------------------------------------------------------------

	int fd = open(dev, O_RDWR);
	if (fd == -1)
	{
		printf("Failed to open device!\n");
		return -1;
	}

	//------------------------------------------------------------
	//    CHECK DEVICE
	//------------------------------------------------------------

	struct fb_var_screeninfo fbvi;
	if (ioctl(fd, FBIOGET_VSCREENINFO, &fbvi) == -1)
	{
		printf("Failed to get VSCREENINFO!\n");
		return -1;
	}

	//------------------------------------------------------------
	//    PREPARATION
	//------------------------------------------------------------

	struct timespec s1, s2, sleep;
	sleep.tv_sec = 0;
	sleep.tv_nsec = 1000000000 / rate;

	//------------------------------------------------------------
	//    CYCLE
	//------------------------------------------------------------

	int i;
	unsigned int elapsed;

	while(1)
	{
		clock_gettime(CLOCK_REALTIME, &s1);

		for (i = 0; i < rate; ++i)
		{
			ioctl(fd, FBIOGET_VSCREENINFO, &fbvi);
			fbvi.activate |= FB_ACTIVATE_NOW | FB_ACTIVATE_FORCE;
			ioctl(fd, FBIOPUT_VSCREENINFO, &fbvi);
			nanosleep(&sleep, NULL);
		}

		clock_gettime(CLOCK_REALTIME, &s2);

		elapsed = 0;
		elapsed += (s2.tv_sec - s1.tv_sec)*1000;
		elapsed += (s2.tv_nsec - s1.tv_nsec)/1000000;

		if (elapsed > 10000)
		{
			sleep.tv_nsec = 1000000000/rate;
		}
		else
		{
			sleep.tv_nsec -= 1000000/rate*(-1000 + elapsed);
		}
	}

	//------------------------------------------------------------
	//    CLEANUP
	//------------------------------------------------------------

	close(fd);

	printf("OK\n");

	return 0;

	//------------------------------------------------------------
}

#include <stdio.h>
#include <time.h>
#include <unistd.h>
int main(){
    int x = 683, y = 384;
FILE *input = fopen("/dev/input/mouse0","r");
FILE *log = fopen("/var/log/mouse_log", "a");
signed char char_num;
signed char protocol[3];
    while(input){// tests to see if file exists
        for(char_num = 0; char_num <3; char_num++){
            protocol[char_num] = fgetc(input);
        }
        x+=protocol[1]; 
        if(x >1366)x = 1366;
        if(x < 0)x = 0;
        y-=protocol[2];
        if(y > 768)y = 768;
        if(y < 0)y = 0;
        // I'm still not entirely sure how to decode the mouse buttons but in the future it will likely be easier to user numbers than words anyway
        // assuming protocol -1 when device is unplugged
        while(protocol[0] == -1){
            sleep(1);
            input = fopen("/dev/input/mouse0","r");
            if(input)
                break;
        }
    if(protocol[0] != -1)
        fprintf(log, "%d %d %d %d\n", (int)time(NULL), protocol[0], x, y);       
    }
    fclose(input);
    fclose(log);
}

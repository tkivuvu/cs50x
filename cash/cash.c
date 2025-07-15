#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int c_o;
    do
    {
        c_o = get_int("Change Owed: ");
    }
    while (c_o < 1);
    int twofive = 0;
    int ten = 0;
    int five = 0;
    int one = 0;
    while (c_o > 0)
        if (c_o >= 25)
        {
            c_o -= 25;
            twofive++;
        }

        else if (c_o >= 10)
        {
            c_o -= 10;
            ten++;
        }

        else if (c_o >= 5)
        {
            c_o -= 5;
            five++;
        }

        else
        {
            c_o -= 1;
            one++;
        }
    printf("%i\n", twofive + ten + five + one);
}

#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int only_digits(string s);
char rotate(char c, int n);

int main(int argc, string argv[])
{
    if (argc != 2)
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    else if (!only_digits(argv[1]))
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
    else
    {
        int key = atoi(argv[1]);
        string plaintext = get_string("plaintext: ");
        int length = strlen(plaintext);
        printf("ciphertext: ");
        for (int i = 0; i < length; i++)
        {
            char current_char = rotate(plaintext[i], key);
            printf("%c", current_char);
        }
        printf("\n");
        return 0;
    }
}

int only_digits(string s)
{
    int length_s = strlen(s);
    for (int k = 0; k < length_s; k++)
    {
        char current_char2 = s[k];
        if (!isdigit(current_char2))
        {
            return false;
        }
    }
    return true;
}

char rotate(char c, int n)
{
    if (isalpha(c) && islower(c))
    {
        c = c - 'a';
        c = c + n;
        c = c % 26;
        c = c + 'a';
        return c;
    }
    else if (isalpha(c) && isupper(c))
    {
        c = c - 'A';
        c = c + n;
        c = c % 26;
        c = c + 'A';
        return c;
    }
    else if (!isalpha(c))
    {
        return c;
    }
    else
    {
        return c;
    }
}

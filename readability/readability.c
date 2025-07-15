#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    string text = get_string("Text: ");
    int length = strlen(text);
    int counter_l = 0;
    int counter_w = 0;
    int counter_s = 0;

    for (int i = 0; i < length; i++)
    {
        if (isalpha(text[i]))
        {
            counter_l++;
        }
    }
    for (int j = 0; j < length; j++)
    {
        if (isblank(text[j]))
        {
            counter_w++;
        }
    }
    for (int k = 0; k < length; k++)
    {
        if (text[k] == '.' || text[k] == '!' || text[k] == '?')
        {
            counter_s++;
        }
    }
    float avg_letters = (float) counter_l / (counter_w + 1) * 100;
    float avg_sentences = (float) counter_s / (counter_w + 1) * 100;
    float coleman_liau_i = 0.0588 * avg_letters - 0.296 * avg_sentences - 15.8;
    if (coleman_liau_i < 1)
    {
        printf("Before Grade 1\n");
    }
    else if (coleman_liau_i > 15)
    {
        printf("Grade 16+\n");
    }
    else
    {
        printf("Grade %i\n", (int) round(coleman_liau_i));
    }
}

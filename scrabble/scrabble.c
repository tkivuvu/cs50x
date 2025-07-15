#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>

int main(void)
{
    string player_1 = get_string("Player 1: ");
    string player_2 = get_string("Player 2: ");
    int length_1 = strlen(player_1);
    int length_2 = strlen(player_2);
    char letters[] = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                      'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'};
    int values[] = {1, 3, 3, 2, 1, 4, 2, 4, 1, 8, 5, 1, 3, 1, 1, 3, 10, 1, 1, 1, 1, 4, 4, 8, 4, 10};
    int player1_sum = 0;
    int player2_sum = 0;
    for (int i = 0; i < length_1; i++)
    {
        char current_char1 = toupper(player_1[i]);
        if (isalpha(current_char1))
        {
            for (int j = 0; j < 27; j++)
            {
                if (letters[j] == current_char1)
                {
                    player1_sum += values[j];

                    break;
                }
            }
        }
    }

    for (int k = 0; k < length_2; k++)
    {
        char current_char2 = toupper(player_2[k]);
        if (isalpha(current_char2))
        {
            for (int l = 0; l < 27; l++)
            {
                if (letters[l] == current_char2)
                {
                    player2_sum += values[l];
                    break;
                }
            }
        }
    }

    if (player1_sum > player2_sum)
    {
        printf("Player 1 wins!\n");
    }
    else if (player2_sum > player1_sum)
    {
        printf("Player 2 wins!\n");
    }
    else
    {
        printf("Tie!\n");
    }
}

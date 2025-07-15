#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

const int header_size = 512;

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        printf("Usage: ./recover FILE.\n");
        return 1;
    }

    FILE *card = fopen(argv[1], "r");
    if (card == NULL)
    {
        printf("Could not open file.\n");
        return 1;
    }
    uint8_t buffer[header_size];
    int file_number = 0;
    char *filename = malloc(8);
    FILE *img = img;
    img = NULL;
    while (fread(&buffer, 1, header_size, card) == header_size)
    {
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff &&
            (buffer[3] & 0xf0) == 0xe0)
        {
            if (img != NULL)
            {
                fclose(img);
            }
            sprintf(filename, "%03i.jpg", file_number);
            file_number += 1;
            img = fopen(filename, "w");
        }
        if (img != NULL)
        {
            fwrite(&buffer, header_size, 1, img);
        }
    }
    fclose(card);
    if (img != NULL)
    {
        fclose(img);
    }
    free(filename);
}

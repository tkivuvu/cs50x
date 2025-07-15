#include <math.h>

#include "helpers.h"

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            RGBTRIPLE pixel = image[i][j];
            BYTE red = pixel.rgbtRed;
            BYTE green = pixel.rgbtGreen;
            BYTE blue = pixel.rgbtBlue;
            float average = (red + green + blue) / 3.0;
            average = round(average);
            image[i][j].rgbtRed = average;
            image[i][j].rgbtGreen = average;
            image[i][j].rgbtBlue = average;
        }
    }
    return;
}

// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            RGBTRIPLE pixel = image[i][j];
            BYTE red = pixel.rgbtRed;
            BYTE green = pixel.rgbtGreen;
            BYTE blue = pixel.rgbtBlue;
            float Red = .393 * red + .769 * green + .189 * blue;
            float Green = .349 * red + .686 * green + .168 * blue;
            float Blue = .272 * red + .534 * green + .131 * blue;
            Red = round(Red);
            Green = round(Green);
            Blue = round(Blue);
            if (Red > 255)
            {
                Red = 255;
            }
            if (Green > 255)
            {
                Green = 255;
            }
            if (Blue > 255)
            {
                Blue = 255;
            }
            image[i][j].rgbtRed = Red;
            image[i][j].rgbtGreen = Green;
            image[i][j].rgbtBlue = Blue;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width / 2; j++)
        {
            RGBTRIPLE pixel = image[i][j];
            image[i][j] = image[i][width - 1 - j];
            image[i][width - 1 - j] = pixel;
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE copy[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j] = image[i][j];
            float red = 0.0;
            float green = 0.0;
            float blue = 0.0;
            float counter = 0.0;
            float avg_red = 0.0;
            float avg_green = 0.0;
            float avg_blue = 0.0;
            for (int k = -1; k <= 1; k++)
            {
                for (int l = -1; l <= 1; l++)
                {
                    int ni = i + k;
                    int nj = j + l;

                    if (ni >= 0 && ni < height && nj >= 0 && nj < width)
                    {
                        counter += 1.0;
                        RGBTRIPLE valid_pixel = image[ni][nj];
                        red += valid_pixel.rgbtRed;
                        green += valid_pixel.rgbtGreen;
                        blue += valid_pixel.rgbtBlue;
                    }
                }
            }
            avg_red = red / counter;
            avg_green = green / counter;
            avg_blue = blue / counter;
            avg_red = round(avg_red);
            avg_green = round(avg_green);
            avg_blue = round(avg_blue);
            copy[i][j].rgbtRed = avg_red;
            copy[i][j].rgbtGreen = avg_green;
            copy[i][j].rgbtBlue = avg_blue;
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j].rgbtRed = copy[i][j].rgbtRed;
            image[i][j].rgbtGreen = copy[i][j].rgbtGreen;
            image[i][j].rgbtBlue = copy[i][j].rgbtBlue;
        }
    }
    return;
}

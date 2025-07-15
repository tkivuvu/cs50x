// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
} node;

// TODO: Choose number of buckets in hash table
const unsigned int N = 143091;

// Hash table
node *table[N];

// this global variable was added by me so as to use it in both
// load and size functions
unsigned int counter = 0;

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // TODO
    // hashes the word i.e gives you its index at that location
    unsigned int bucket = hash(word);
    // this is the head of the linked list
    node *cursor = table[bucket];
    while (cursor != NULL)
    {
        // this compares the word with the current node's word
        if (strcasecmp(cursor->word, word) == 0)
        {
            return true;
        }
        // this moves the cursor to the next node
        cursor = cursor->next;
    }
    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    // TODO: Improve this hash function
    int sum = 0;
    for (int i = 0; word[i] != '\0'; i++)
    {
        sum += tolower(word[i]);
    }
    return sum % N;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // TODO
    FILE *dict_ = fopen(dictionary, "r");
    char buffer[LENGTH + 1];
    if (dict_ == NULL)
    {
        return false;
    }
    unsigned int result = fscanf(dict_, "%s", buffer);
    while (result != EOF)
    {
        node *new_node = malloc(sizeof(node));
        if (new_node == NULL)
        {
            return false;
        }
        strcpy(new_node->word, buffer);
        new_node->next = NULL;
        unsigned int bucket = hash(buffer);
        new_node->next = table[bucket];
        table[bucket] = new_node;
        counter += 1;
        result = fscanf(dict_, "%s", buffer);
    }
    fclose(dict_);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    // TODO
    return counter;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    // TODO
    for (int i = 0; i < N; i++)
    {
        node *ptr = table[i];
        while (ptr != NULL)
        {
            node *temp = ptr;
            ptr = ptr->next;
            free(temp);
        }
    }
    return true;
}

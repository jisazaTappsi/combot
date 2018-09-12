"""
Values are added here and not in txt files due to encoding issues
"""


def get_groups():
    with open('groups.txt', 'r', encoding='utf-8') as f:
        return [(line.split(',')[0], line.split(',')[1], int(line.split(',')[2])) for line in f.read().split('\n')]


def get_keywords():
    with open('keywords.txt', 'r', encoding='utf-8') as f:
        return [line.split(',')[0] for line in f.read().split('\n')]


def get_groups_to_publish():
    with open('groups_to_publish.txt', 'r', encoding='utf-8') as f:
        return [(line.split(',')[0], line.split(',')[1]) for line in f.read().split('\n')]


if __name__ == '__main__':
    get_groups()
    get_keywords()
    get_groups_to_publish()

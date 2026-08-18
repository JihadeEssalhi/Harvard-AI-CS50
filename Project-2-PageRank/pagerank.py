import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    N = len(corpus)
    distribution = {}
    
    # If page has no outgoing links, probability is uniform across all pages
    if len(corpus[page]) == 0:
        for p in corpus:
            distribution[p] = 1 / N
        return distribution
    
    # Initialize all pages with probability (1 - damping_factor) / N
    random_prob = (1 - damping_factor) / N
    for p in corpus:
        distribution[p] = random_prob
    
    # Add probability from following links
    link_prob = damping_factor / len(corpus[page])
    for link in corpus[page]:
        distribution[link] += link_prob
    
    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    page_ranks = {page: 0 for page in corpus}
    
    # First sample: choose a page at random
    current_page = random.choice(list(corpus.keys()))
    page_ranks[current_page] += 1
    
    # Generate remaining samples
    for _ in range(n - 1):
        # Get transition probabilities from current page
        probs = transition_model(corpus, current_page, damping_factor)
        
        # Choose next page based on probabilities
        pages = list(probs.keys())
        probabilities = list(probs.values())
        next_page = random.choices(pages, weights=probabilities, k=1)[0]
        
        # Update counts
        page_ranks[next_page] += 1
        current_page = next_page
    
    # Normalize to get probabilities
    for page in page_ranks:
        page_ranks[page] /= n
    
    return page_ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    
    # Initialize all pages with equal probability
    page_ranks = {page: 1 / N for page in corpus}
    
    # Handle pages with no links
    # If a page has no links, treat it as having links to all pages
    for page in corpus:
        if len(corpus[page]) == 0:
            corpus[page] = set(corpus.keys())
    
    # Iterate until convergence
    while True:
        new_ranks = {}
        max_change = 0
        
        for page in corpus:
            # Start with random probability
            rank = (1 - damping_factor) / N
            
            # Add probability from pages that link to this page
            for linking_page in corpus:
                if page in corpus[linking_page]:
                    rank += damping_factor * (page_ranks[linking_page] / len(corpus[linking_page]))
            
            new_ranks[page] = rank
            max_change = max(max_change, abs(rank - page_ranks[page]))
        
        # Check for convergence
        if max_change < 0.001:
            break
        
        page_ranks = new_ranks
    
    return page_ranks


if __name__ == "__main__":
    main()
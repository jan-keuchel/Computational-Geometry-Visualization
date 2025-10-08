# Computational geometry visualization
## About this project
In the fall semester of 2025/2026 I am taking a course on computational geometry called "Grafisch-geometrische Algorithmen".
The aim for this project is to:
- Learn Python.
- Deepen my understanding of the algorithms covered in the lecture and the accompanying book.
- Implement and visualize the algorithms.

## Topics
The topics of the lecture are the following:
- Convex Hulls
- Line Segment Intersection
- Triangulation
- Orthogonal Range Searching
- Point Location
- Voronoi Diagrams
- Delaunay Triangulations

As of now, I don't know to which of the topics I'll be visualizing the algorithms for.
This is because I do not know about the algorithms, yet.

## Progress
To document the progress I've done so far and list some other things I need to do in order to visualize certain algorithms, here's a list of things I'm working on:
- [ ] Generation of graphs on which the algorithms will be visualized
    - [x] Fully connected graph
    - [x] MST
    - [x] MST with additional edges on nodes n with originally deg(n) = 1
    - [ ] Triangulation
- [ ] Convex Hulls
    - [x] Brute force approach
        - [x] Algorithm itself
        - [x] Visualization with animation
    - [x] Graham's scan
        - [x] Algorithm itself
        - [x] Visualization with animation
    - [ ] Gift wrapping (Jarvis March)
        - [ ] Algorithm itself
        - [ ] Visualization with animation
- [ ] Line Segment Intersection
- [ ] Triangulation
- [ ] Orthogonal Range Searching
- [ ] Point Location
- [ ] Voronoi Diagrams
- [ ] Delaunay Triangulations
- [ ] Convenience
    - [ ] Control via keyboard input
         - [ ] Reset graph (new random graph)
         - [ ] Select algorithm to apply
         - [ ] start simulation
- [ ] Others
    - [x] MST, Prims

### Questions
- [ ] How do I properly visualize the algorithms?
    - [ ] Short break after each step of the algorithm to draw new state
    - [ ] How do I manage the colors of edges, nodes, etc? Via intern state of extern color?

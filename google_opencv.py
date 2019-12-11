import cv2

def google_API(path):
    """Localize objects in the local image.

    Args:
    path: The path to the local file.
    """
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    with open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    # for object_ in objects:
    #     print('\n{} (confidence: {})'.format(object_.name, object_.score))
    #     print('Normalized bounding polygon vertices: ')
    #     for vertex in object_.bounding_poly.normalized_vertices:
    #         print(' - ({}, {})'.format(vertex.x, vertex.y))
    return objects


def localizar_objetos(frame):
    # (x, y, w, h, label)
    img_name = "opencv_frame.png"
    cv2.imwrite(img_name, frame)
    response = google_API(img_name)

    saida = list()
    dim_x = frame.shape[0]
    dim_y = frame.shape[1]

    for o in response:
        print('\n{} (confidence: {})'.format(o.name, o.score))
        print('Normalized bounding polygon vertices: ')
        label = o.name
        vertice_1 = o.bounding_poly.normalized_vertices[0]
        vertice_2 = o.bounding_poly.normalized_vertices[2]
        x = vertice_1.x * dim_x
        y = vertice_1.y * dim_y
        w = vertice_2.x * dim_x - x
        h = vertice_2.y * dim_y - y
        elemento = (x, y, w, h, label)
        saida.append(elemento)

    return saida

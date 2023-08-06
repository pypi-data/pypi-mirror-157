{{SLASH_COMMENTS}}

#include <QDebug>

#include "image_provider.h"

QmlImageProvider::QmlImageProvider()
    : QQuickImageProvider(QQuickImageProvider::Image) {
}

void QmlImageProvider::updateImage(int index, const QImage &image) {
    qDebug() << "provider: update" << index;
    QMutexLocker lock(&mutex);
    images[index] = image;
}

void QmlImageProvider::deleteImage(int index) {
    qDebug() << "provider: delete" << index;
    QMutexLocker lock(&mutex);
    images.remove(index);
}

QImage QmlImageProvider::requestImage(const QString &id, QSize *size, const QSize &requestedSize) {
    qDebug() << "provider: request id" << id;
    int index = id.leftRef(id.indexOf("###")).toInt();
    qDebug() << "provider: request index" << index;

    QMutexLocker lock(&mutex);
    QImage image = images[index];
    if (!image.isNull()) {
        image.scaled(requestedSize);
        if (size) *size = requestedSize;
    }

    return image;
}

QmlImageManager::QmlImageManager(QObject *parent) : QObject(parent) {
    qmlImageProvider = new QmlImageProvider();
}

void QmlImageManager::updateImage(int index, const QImage &image) {
    qmlImageProvider->updateImage(index, image);
    emit imageChanged(index);
}

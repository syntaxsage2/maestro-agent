import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { X, Upload, Image as ImageIcon } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface ImageUploadProps {
  onImagesChange: (files: File[]) => void;
  maxImages?: number;
  maxSize?: number;
}

export const ImageUpload = ({
  onImagesChange,
  maxImages = 5,
  maxSize = 10 * 1024 * 1024 // 10MB
}: ImageUploadProps) => {
  const [images, setImages] = useState<File[]>([]);
  const [previews, setPreviews] = useState<string[]>([]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // 检查文件数量
    if (images.length + acceptedFiles.length > maxImages) {
      toast.error(`最多只能上传 ${maxImages} 张图片`);
      return;
    }

    // 检查文件大小
    const oversizedFiles = acceptedFiles.filter(file => file.size > maxSize);
    if (oversizedFiles.length > 0) {
      toast.error('图片大小不能超过 10MB');
      return;
    }

    // 添加图片
    const newImages = [...images, ...acceptedFiles];
    setImages(newImages);

    // 生成预览
    const newPreviews = acceptedFiles.map(file => URL.createObjectURL(file));
    setPreviews([...previews, ...newPreviews]);

    // 通知父组件
    onImagesChange(newImages);
  }, [images, previews, maxImages, maxSize, onImagesChange]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    },
    maxSize,
  });

  const removeImage = (index: number) => {
    const newImages = images.filter((_, i) => i !== index);
    const newPreviews = previews.filter((_, i) => i !== index);

    // 释放 URL
    URL.revokeObjectURL(previews[index]);

    setImages(newImages);
    setPreviews(newPreviews);
    onImagesChange(newImages);
  };

  return (
    <div className="space-y-3">
      {previews.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {previews.map((preview, index) => (
            <div key={index} className="relative group">
              <img
                src={preview}
                alt={`预览 ${index + 1}`}
                className="w-20 h-20 object-cover rounded-lg border border-gray-700"
              />
              <button
                onClick={() => removeImage(index)}
                className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                aria-label="删除图片"
              >
                <X className="w-3 h-3 text-white" />
              </button>
            </div>
          ))}
        </div>
      )}

      {images.length < maxImages && (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors
            ${isDragActive
              ? 'border-accent bg-accent/10'
              : 'border-gray-700 hover:border-gray-600'
            }
          `}
        >
          <input {...getInputProps()} />
          <div className="flex flex-col items-center gap-2">
            {isDragActive ? (
              <>
                <Upload className="w-6 h-6 text-accent" />
                <p className="text-sm text-accent">松开即可上传图片</p>
              </>
            ) : (
              <>
                <ImageIcon className="w-6 h-6 text-gray-500" />
                <p className="text-sm text-gray-400">
                  点击或拖拽图片到这里上传
                </p>
                <p className="text-xs text-gray-600">
                  支持 JPG、PNG、GIF、WebP，最多 {maxImages} 张
                </p>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

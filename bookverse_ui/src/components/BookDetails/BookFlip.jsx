import { useEffect, useRef, useState } from "react";
import * as pdfjsLib from "pdfjs-dist";
import HTMLFlipBook from "react-pageflip";
import { Loader2 } from "lucide-react";
import { useParams } from 'react-router-dom';
import { minio_link } from "../../backend_links";

pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

export default function BookFlip() {
  const {id} = useParams();
  const [pdf, setPdf] = useState(null);
  const [numPages, setNumPages] = useState(0);
  const [currentPage, setCurrentPage] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [pageImages, setPageImages] = useState({});
  const bookRef = useRef();

  useEffect(() => {
    const loadPdf = async () => {
      const loadingTask = pdfjsLib.getDocument(`${minio_link}/book-pdfs/${id}.pdf`);
      const loadedPdf = await loadingTask.promise;
      setPdf(loadedPdf);
      setNumPages(loadedPdf.numPages);
      setIsLoading(false);

      preloadPages(0, loadedPdf);
    };

    loadPdf();
  }, []);

  const preloadPages = async (pageIndex, loadedPdf = pdf) => {
    if (!loadedPdf) return;
    const indicesToLoad = [pageIndex - 1, pageIndex, pageIndex + 1].filter(
      (i) => i >= 0 && i < loadedPdf.numPages
    );

    for (const i of indicesToLoad) {
      if (!pageImages[i]) {
        const page = await loadedPdf.getPage(i + 1);
        const viewport = page.getViewport({ scale: 1.5 });

        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        canvas.width = viewport.width;
        canvas.height = viewport.height;

        await page.render({ canvasContext: context, viewport }).promise;

        setPageImages((prev) => ({
          ...prev,
          [i]: canvas.toDataURL(),
        }));
      }
    }
  };

  const handleNext = () => {
    bookRef.current.pageFlip().flipNext();
  };

  const handlePrev = () => {
    bookRef.current.pageFlip().flipPrev();
  };

  const onFlip = async (e) => {
    const newPage = e.data;
    setCurrentPage(newPage + 1);
    preloadPages(newPage);
  };

  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center py-8">
        {isLoading ? (
            <div className="flex flex-col items-center text-gray-500">
            <Loader2 className="animate-spin mb-2" size={32} />
            Loading book...
            </div>
        ) : (
            <>
            {/* Book with frame */}
            <div className="border-4 border-gray-300 rounded-xl shadow-xl overflow-hidden">
                <HTMLFlipBook
                width={600}
                height={800}
                ref={bookRef}
                onFlip={onFlip}
                className="bg-white"
                >
                {Array.from({ length: numPages }, (_, i) => (
                    <div key={i} className="page p-2 bg-white flex items-center justify-center">
                    {pageImages[i] ? (
                        <img
                        src={pageImages[i]}
                        alt={`Page ${i + 1}`}
                        className="w-full h-full object-contain"
                        />
                    ) : (
                        <div className="text-gray-400">Loading...</div>
                    )}
                    </div>
                ))}
                </HTMLFlipBook>
            </div>

            {/* Navigation buttons */}
            <div className="mt-6 flex justify-center items-center gap-4">
                <button
                onClick={handlePrev}
                className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                >
                Previous
                </button>
                <span className="text-lg font-medium">
                Page {currentPage} / {numPages}
                </span>
                <button
                onClick={handleNext}
                className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
                >
                Next
                </button>
            </div>
            </>
        )}
    </div>
  );
}

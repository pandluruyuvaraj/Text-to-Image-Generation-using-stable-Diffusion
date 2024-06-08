document.addEventListener("DOMContentLoaded", function() {
  const generateBtn = document.querySelector(".generate-btn");
  const promptInput = document.querySelector(".prompt-input");
  const generatedImage = document.querySelector(".generated-image");
  const downloadBtn = document.querySelector(".download-btn");
  const imageDataInput = document.querySelector("#image-data");

  const showNotification = (message) => {
      alert(message);
  };


  const generateImage = async () => {
      const prompt = promptInput.value;

      if (prompt) {
          try {
              generatedImage.src = "static/p.gif";

              const response = await fetch("/generate", {
                  method: "POST",
                  headers: {
                      "Content-Type": "application/x-www-form-urlencoded",
                  },
                  body: new URLSearchParams({ data: prompt }),
              });

              if (!response.ok) {
                  throw new Error("Failed to generate image.");
              }

              const imageData = await response.text();
              generatedImage.src = "data:image/png;base64," + imageData;
              imageDataInput.value = imageData; // Set the image data in the hidden input
              downloadBtn.disabled = false; // Enable the download button
          } catch (error) {
              console.error(error);
              generatedImage.src = "static/image-placeholder.png";
              downloadBtn.disabled = true; // Disable the download button on error
          }
      } else {
          showNotification("Please enter the prompt");
      }
  };

  generateBtn.addEventListener("click", generateImage);

  // When the download button is clicked, submit the hidden form to download the image
});

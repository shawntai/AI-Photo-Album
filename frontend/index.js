// solve: Uncaught ReferenceError: apigClientFactory is not defined at index.js:5:20
// const apigClientFactory = require("./apiGateway-js-sdk/apigClient").default;
// const apigClient = apigClientFactory.newClient();

const API_URL = "https://1rup48u854.execute-api.us-east-1.amazonaws.com/v1";

const recordButton = document.querySelector("#record");
const transcriptInput = document.querySelector("#transcript");

window.SpeechRecognition =
	window.webkitSpeechRecognition || window.SpeechRecognition;
const recognition = new window.SpeechRecognition();
recognition.interimResults = true;

let finalTranscript = "";
let isRecording = false;

recognition.addEventListener("result", (e) => {
	const transcript = Array.from(e.results)
		.map((result) => result[0])
		.map((result) => result.transcript)
		.join("");

	if (e.results[0].isFinal) {
		finalTranscript += transcript;
	}
});

recognition.addEventListener("end", () => {
	transcriptInput.value = finalTranscript;
});

recordButton.addEventListener("click", () => {
	if (isRecording) {
		recognition.stop();
		recordButton.textContent = "Start Recording";
	} else {
		finalTranscript = "";
		recognition.start();
		recordButton.textContent = "Stop Recording";
	}
	isRecording = !isRecording;
});

const searchButton = document.querySelector("#search");
searchButton.addEventListener("click", () => {
	const transcript = transcriptInput.value;
	console.log(transcript);
	// make a get call to this url ${API_URL}/search?q=${transcript} and print the response body
	fetch(`${API_URL}/search?q=${transcript}`, {
		method: "GET",
	})
		.then((response) => response.json())
		.then((data) => {
			console.log(data);
			const results = document.querySelector("#results");
			results.innerHTML = "";
			data.results.forEach((item) => {
				const div = document.createElement("div");
				const img = document.createElement("img");
				img.style.height = "200px";
				img.style.float = "left";
				img.style.margin = "5px";
				img.src = item;
				div.appendChild(img);
				results.appendChild(div);
			});
		});
});

const uploadButton = document.querySelector("#upload");
uploadButton.addEventListener("click", () => {
	const file = document.querySelector("#file").files[0];
	const customLabels = document.querySelector("#custom_labels");
	console.log(file);
	const fileName = file.name;
	const customLabelsValue = customLabels.value;
	console.log(fileName);
	console.log(file);
	console.log(customLabelsValue);
	customLabels.value = "";

	// check if file type is jpg, png, or jpeg. if not, alert user to upload a valid file type; else, read the file using the FileReader.readAsBinaryString function and btoa function and upload the file to S3 via the API Gateway method (uploadPut)
	//  check if file type is jpg, png, or jpeg
	//  if not, alert user to upload a valid file type
	//  else, read the file using the FileReader.readAsBinaryString function and btoa function and upload the file to S3 via the API Gateway method (uploadPut)
	if (
		file.type !== "image/jpeg" &&
		file.type !== "image/png" &&
		file.type !== "image/jpg"
	) {
		alert("Please upload a valid file type (jpg, png, or jpeg)");
	} else {
		const reader = new FileReader();
		reader.onload = () => {
			// const base64Img = btoa(event.target.result);
			// console.log(base64Img);
			console.log(reader.result);
			fetch(
				`${API_URL}/upload`,
				// "https://we08oh48pc.execute-api.us-east-1.amazonaws.com/v1/upload",
				{
					method: "PUT",
					headers: {
						"Content-Type": file.type,
						bucket: "cs6998-hw2-b2",
						key: fileName,
						"x-amz-meta-customLabels": customLabelsValue,
					},
					body: reader.result,
				}
			)
				// fetch(
				// 	"https://1rup48u854.execute-api.us-east-1.amazonaws.com/v1/status",
				// 	{
				// 		method: "GET",
				// 	}
				// )
				.then((response) => {
					console.log(response);
				})
				.catch((err) => {
					console.log(err);
				});

			// 	// apigClient
			// 	// 	.uploadPut(
			// 	// 		{
			// 	// 			Accept: "*/*",
			// 	// 			"Access-Control-Allow-Origin": "*",
			// 	// 			"Content-Type": file.type,
			// 	// 			bucket: "cs6998-hw2-b2",
			// 	// 			key: fileName,
			// 	// 			"x-amz-meta-customLabels": customLabelsValue,
			// 	// 		},
			// 	// 		base64Img,
			// 	// 		{
			// 	// 			// Headers: {
			// 	// 			// 	"Access-Control-Allow-Origin": "*",
			// 	// 			// 	"Content-Type": file.type,
			// 	// 			// },
			// 	// 		}
			// 	// 	)
			// 	// 	.then((result) => {
			// 	// 		console.log(result);
			// 	// 	})
			// 	// 	.catch((err) => {
			// 	// 		console.log(err);
			// 	// 	});
		};
		reader.readAsArrayBuffer(file);
		// fetch(
		// 	"https://1rup48u854.execute-api.us-east-1.amazonaws.com/v1/upload",
		// 	{
		// 		method: "PUT",
		// 		headers: {
		// 			Accept: "*/*",
		// 			"Content-Type": file.type,
		// 			bucket: "cs6998-hw2-b2",
		// 			key: fileName,
		// 			"x-amz-meta-customLabels": customLabelsValue,
		// 			"Access-Control-Allow-Origin": "*",
		// 			"Access-Control-Allow-Methods": "*",
		// 			"Access-Control-Allow-Headers": "*",
		// 		},
		// 		body: file,
		// 	}
		// )
		// 	.then((response) => {
		// 		console.log(response);
		// 	})
		// 	.catch((error) => {
		// 		console.log(error);
		// 	});
	}

	// apigClient
	// 	.uploadPut(
	// 		{
	// 			bucket: "speech-to-text-demo",
	// 			key: fileName,
	// 			"x-amz-meta-customLabels": customLabelsValue,
	// 		},
	// 		fileContent,
	// 		{}
	// 	)
	// 	.then((result) => {
	// 		console.log(result);
	// 	})
	// 	.catch((err) => {
	// 		console.log(err);
	// 	});
});

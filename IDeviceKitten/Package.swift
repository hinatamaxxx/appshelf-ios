// swift-tools-version: 5.9
import PackageDescription

let package = Package(
	name: "IDeviceKit",
	platforms: [
		.iOS(.v15),
		.macOS(.v12),
	],
	products: [
		.library(
			name: "IDevice",
			targets: ["IDevice"]
		),
		.library(
			name: "IDeviceSwift",
			targets: ["IDeviceSwift"]
		),
	],
	targets: [
		.binaryTarget(
			// Made by tools/prepare-idevice.py from the official v0.1.57 release (same checksum as
			// upstream pins), iOS device slice only, without the compiler-rt objects that clash with
			// the SDK's libclang_rt under the LLVM linker. Not committed (about 100 MB).
			name: "IDevice",
			path: "IDevice.xcframework"
		),
		.target(
			name: "IDeviceSwift",
			dependencies: ["IDevice"]
		),
	]
)

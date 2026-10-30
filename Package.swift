// swift-tools-version: 5.9
// AppShelf: Feather's app target as a SwiftPM package, so xtool can build it without Xcode.
import PackageDescription

let package = Package(
    name: "AppShelf",
    platforms: [.iOS(.v16)],
    products: [.library(name: "AppShelf", targets: ["AppShelf"])],
    dependencies: [
        .package(path: "AltSourceKit"),
        .package(path: "NimbleKit"),
        .package(path: "Zsign"),
        .package(path: "IDeviceKitten"),
        .package(url: "https://github.com/vapor/vapor", exact: "4.104.0"),
        .package(url: "https://github.com/kean/Nuke", exact: "12.8.0"),
        .package(url: "https://github.com/marmelroy/Zip", exact: "2.1.2"),
        .package(url: "https://github.com/tsolomko/SWCompression", exact: "4.8.7"),
    ],
    targets: [
        .target(name: "FeatherObjC", path: "FeatherObjC"),
        .target(
            name: "AppShelf",
            dependencies: [
                "FeatherObjC",
                .product(name: "AltSourceKit", package: "AltSourceKit"),
                .product(name: "NimbleExtensions", package: "NimbleKit"),
                .product(name: "NimbleJSON", package: "NimbleKit"),
                .product(name: "NimbleViews", package: "NimbleKit"),
                .product(name: "Zsign", package: "Zsign"),
                .product(name: "zsignc", package: "Zsign"),
                .product(name: "IDeviceSwift", package: "IDeviceKitten"),
                .product(name: "Vapor", package: "vapor"),
                .product(name: "Nuke", package: "Nuke"),
                .product(name: "NukeUI", package: "Nuke"),
                .product(name: "Zip", package: "Zip"),
                .product(name: "SWCompression", package: "SWCompression"),
            ],
            path: "Feather",
            exclude: [
                "Resources/Info.plist",
                "Resources/Launch Screen.storyboard",
                "Supporting Files",
                // An ar archive: SwiftPM would run strip on it. Added to the app root after the build.
                "Resources/ellekit.deb",
            ],
            resources: [
                .process("Resources/Assets.xcassets"),
                .process("Resources/Localizable.xcstrings"),
                .process("Backend/Storage/Feather.xcdatamodeld"),
                .copy("Resources/feather_extension.png"),
                .copy("Resources/Icons"),
            ],
            linkerSettings: [.unsafeFlags(["-Xlinker", "-platform_version", "-Xlinker", "ios",
                                            "-Xlinker", "16.0", "-Xlinker", "27.0"])]
        ),
    ],
    swiftLanguageVersions: [.v5]
)

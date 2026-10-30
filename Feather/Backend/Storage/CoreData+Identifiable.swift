//
//  CoreData+Identifiable.swift
//  AppShelf
//
//  Xcode's generated Core Data classes declare Identifiable; the Linux momc stand-in used by the
//  xtool build leaves it out for these two, which SwiftUI lists and sheets need.
//

import CoreData

extension AltSource: Identifiable {}
extension CertificatePair: Identifiable {}

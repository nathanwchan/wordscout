// Copyright (c) 2010 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// A generic onclick callback function.
function genericOnClick(info, tab) {
	if( info.selectionText ){
		//chrome.contextMenus.update(menuItemId, {
        //title: 'Word Scout',
        //contexts: ["selection"],
        //onclick: genericOnClick
		console.log('called');
		chrome.tabs.create({url: "http://127.0.0.1:5000/"+ info.selectionText});
    };	
}

// Create one test item for each context type.
var contexts = ["selection"];
for (var i = 0; i < contexts.length; i++) {
  var context = contexts[i];
  var title = 'Word Scout';
  var id = chrome.contextMenus.create({"title": title, "contexts":[context],
                                       "onclick": genericOnClick});
  console.log("'" + context + "' item:" + id);
}



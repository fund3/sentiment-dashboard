angular.module('BitcoinSentimentsApp', [])
.factory('BitcoinSentimentsService', ['$q', '$rootScope', function($q, $rootScope) {
  var Service = {}

  Service.getTweetsFromServer = function() {
      url = '/get_tweets.json'
      var promise = fetch(url)
      return promise;
  }

  return Service;
}])
.controller('TweetTableController', function($scope, BitcoinSentimentsService) {
    var tweetTable = this;

    tweetTable.tweets = [
      {'id_str': 10001012201, 'created_at': '2019-01-01 00:00:01', 'full_text': 'Tweet number 1', 'subjectivity': 0.0, 'polarity': -1.0},
      {'id_str': 19111989189, 'created_at': '2025-03-03 01:00:01', 'full_text': 'Tweet number 2', 'subjectivity': 0.5, 'polarity': 0.8}
    ];

    tweetTable.getTweets = function() {
      tweetTable.tweets = [
        {'id_str': 1, 'full_text': 'working!'}
      ]

      console.log('datatable: ' + datatable)

      datatable.destroy()

      document.getElementById("output").innerHTML = "";

      BitcoinSentimentsService.getTweetsFromServer()
      .then(function(response) {
        return response.json();
      }).then(function(data) {
        console.log('in callback')
        Bokeh.embed.embed_item(data['plot'])
        Bokeh.embed.embed_item(data['plot2'])

        console.log(data['tweets'])
        tweetTable.tweets = data['tweets']
        $scope.$apply();

        datatable = $('#id_tweet_table').DataTable();

        console.log('done: ' + JSON.stringify(tweetTable.tweets))
      })
    };

});

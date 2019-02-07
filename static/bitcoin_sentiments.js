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

    tweetTable.showTimeline = function() {
        if($('#card_li_plot a').hasClass('bs_timeline_empty') && $('#card_li_intro a').hasClass('active')) {
            $('#card_li_intro a').removeClass('active')
            $('#card_li_plot a').addClass('active')
            $('#card_body_intro').css('display', 'none')
            $('#card_body_plot').css('display', 'block')

            tweetTable.tweets = [
                {'id_str': 1, 'full_text': 'working!'}
            ]

            BitcoinSentimentsService.getTweetsFromServer()
            .then(function(response) {
                return response.json()
            }).then(function(data) {
                $('#plot_card_spinner').css('display', 'none')
                Bokeh.embed.embed_item(data['plot2'], 'mainplot_div')
                tweetTable.tweets = data['tweets']
                $('#card_li_plot a').removeClass('bs_timeline_empty')
                $scope.$apply();
            })
        } else {
            $('#card_li_intro a').removeClass('active')
            $('#card_li_plot a').addClass('active')
            $('#card_body_intro').css('display', 'none')
            $('#card_body_plot').css('display', 'block')
        }
    };

    tweetTable.getIntro = function() {
        if($('#card_li_plot a').hasClass('active')) {
            $('#card_li_plot a').removeClass('active')
            $('#card_li_intro a').addClass('active')
            $('#card_body_plot').css('display', 'none')
            $('#card_body_intro').css('display', 'block')
        }
    };

});

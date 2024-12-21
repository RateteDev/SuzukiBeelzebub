import re

class MessageCleaner:
    @staticmethod
    def remove_urls(text):
        """URLを削除する関数"""
        return re.sub(r'http[s]?://\S+', '', text)
    
    @staticmethod
    def remove_custom_emojis(text):
        """Discordのカスタム絵文字を削除する関数"""
        return re.sub(r'<a?:\w+:\d+>', '', text)

    @staticmethod
    def remove_unicode_emojis(text):
        """ユニコードの絵文字を削除する関数"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # 笑顔の絵文字
            "\U0001F300-\U0001F5FF"  # シンボル & 絵文字
            "\U0001F680-\U0001F6FF"  # 乗り物 & 絵文字
            "\U0001F1E0-\U0001F1FF"  # 旗の絵文字
            "\U00002702-\U000027B0"  # その他の記号
            "\U000024C2-\U0001F251"  # Enclosed characters
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)

    @staticmethod
    def remove_mentions(text):
        """メンションを削除する関数"""
        text = re.sub(r'<@!?&?\d+>', '', text)
        return re.sub(r'@\w+', '', text)

    @staticmethod
    def clean_text(text):
        """全てのクリーニング処理を適用"""
        text = MessageCleaner.remove_urls(text)
        text = MessageCleaner.remove_custom_emojis(text)
        text = MessageCleaner.remove_mentions(text)
        return text
